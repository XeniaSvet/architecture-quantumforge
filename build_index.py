import time
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

KB_DIR = Path("knowledge_base")
INDEX_DIR = Path("faiss_index")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_and_chunk_documents() -> list[Document]:
    md_files = sorted(KB_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"Папка {KB_DIR} пуста или не найдена!")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # ~150-200 слов (оптимально для e5-large, лимит 512 токенов)
        chunk_overlap=150,    # перекрытие ~15% для сохранения контекста на стыках
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Document] = []

    for file_path in md_files:
        raw_text = file_path.read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        # Извлекаем метаданные из шапки документа (Entity и Category)
        entity = file_path.stem
        category = "unknown"
        body_lines = []

        for line in lines:
            if line.startswith("Entity:"):
                entity = line.replace("Entity:", "").strip()
            elif line.startswith("Category:"):
                category = line.replace("Category:", "").strip()
            else:
                body_lines.append(line)

        clean_body = "\n".join(body_lines).strip()
        text_chunks = splitter.split_text(clean_body)

        for idx, chunk_text in enumerate(text_chunks):
            prefixed_text = f"{entity}. {chunk_text}"
            doc = Document(
                page_content=prefixed_text,
                metadata={
                    "source": str(file_path).replace("\\", "/"),
                    "entity": entity,
                    "category": category,
                    "chunk_id": idx,
                    "raw_text": chunk_text,
                },
            )
            all_chunks.append(doc)

    return all_chunks


def main():
    start_time = time.time()
    print("1. Загрузка и разбиение документов на чанки...")
    chunks = load_and_chunk_documents()
    print(f"   Загружено документов: {len(list(KB_DIR.glob('*.md')))}")
    print(f"   Сформировано чанков: {len(chunks)}")

    print(f"\n2. Загрузка модели эмбеддингов ({MODEL_NAME})...")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print("\n3. Генерация эмбеддингов и построение индекса FAISS...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))
    elapsed = time.time() - start_time

    print(f"\n[ГОТОВО] Индекс успешно сохранён в папку: {INDEX_DIR}/")
    print(f"Общее время генерации: {elapsed:.2f} сек.")

    # 4. Тестовый прогон поиска по индексу
    print("\n" + "=" * 60)
    print("ТЕСТОВЫЕ ЗАПРОСЫ К ВЕКТОРНОМУ ИНДЕКСУ")
    print("=" * 60)

    test_queries = [
        "Кто такой Княжич Мирослав и чьим сыном он является?",
        "Как работает техника Вихревой Удар и кто её создал?",
        "Из-за чего произошло Падение Клана Хранителей Ока?",
    ]

    for q in test_queries:
        print(f"\nЗапрос: «{q}»")
        results = vectorstore.similarity_search_with_score(f"{q}", k=2)
        for rank, (doc, score) in enumerate(results, start=1):
            snippet = doc.metadata.get("raw_text", doc.page_content)[:220].replace("\n", " ")
            print(
                f"  [{rank}] Score (L2 distance): {score:.4f} | "
                f"Сущность: {doc.metadata['entity']} | "
                f"Файл: {doc.metadata['source']} (чанк #{doc.metadata['chunk_id']})"
            )
            print(f"      Текст: {snippet}...")


if __name__ == "__main__":
    main()