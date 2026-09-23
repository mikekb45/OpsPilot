# OpsPilot - builds the Chroma vector index from knowledge/.
#
# Splits each markdown doc into chunks on its "## " section headers,
# then upserts everything into a persistent local collection. Chroma
# embeds the text automatically via its default embedding function -
# nothing here calls an embedding model directly.

import pathlib

import chromadb

KNOWLEDGE_DIR = pathlib.Path("knowledge")


def chunk_markdown(text):
    # Split on "## " section headers. The first piece is the title
    # and intro paragraph - it never had a "## " prefix, so it's left
    # as-is; every later piece needs its heading reattached.
    sections = text.split("## ")

    chunks = [sections[0].strip()]
    for section in sections[1:]:
        heading, _, body = section.partition("\n")
        chunks.append(f"## {heading}\n{body.strip()}")

    return chunks


client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="opspilot_knowledge")

documents, ids, metadatas = [], [], []
file_count = 0
for path in KNOWLEDGE_DIR.glob("*.md"):
    file_count += 1
    chunks = chunk_markdown(path.read_text())
    documents += chunks
    ids += [f"{path.stem}-{i}" for i in range(len(chunks))]
    metadatas += [{"source": path.name} for _ in chunks]

# upsert (not add) - overwrites existing ids instead of erroring, so
# this script stays safe to rerun as knowledge/ changes.
collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
print(f"Indexed {len(documents)} chunks from {file_count} documents.")
