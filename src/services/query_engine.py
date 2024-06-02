import os
import json
import tempfile
import shutil
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from llama_index.core import set_global_service_context, VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.embeddings.gradient import GradientEmbedding
from llama_index.llms.gradient import GradientBaseModelLLM

class QueryEngine:
    def __init__(self):
        secure_connect_path = 'secure-connect/secure-connect-chatbot.zip'
        token_json_path = 'secure-connect/token.json'

        with open(token_json_path) as f:
            secrets = json.load(f)

        CLIENT_ID = secrets["clientId"]
        CLIENT_SECRET = secrets["secret"]

        # Create a temporary directory for the secure connect bundle
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_secure_connect_path = os.path.join(tmpdir, 'secure-connect-chatbot.zip')
            shutil.copy(secure_connect_path, tmp_secure_connect_path)

            auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
            cluster = Cluster(cloud={'secure_connect_bundle': tmp_secure_connect_path}, auth_provider=auth_provider)

            try:
                self.session = cluster.connect()
                row = self.session.execute("select release_version from system.local").one()
                if row:
                    print(f"Cassandra version: {row[0]}")
                else:
                    print("An error occurred.")
            except Exception as e:
                print(f"Unable to connect to Cassandra: {e}")

        self.myllm = GradientBaseModelLLM(base_model_slug="llama2-7b-chat", max_tokens=400)
        self.embed_model = GradientEmbedding(
            gradient_access_token=os.environ.get("GRADIENT_ACCESS_TOKEN"),
            gradient_workspace_id=os.environ.get("GRADIENT_WORKSPACE_ID"),
            gradient_model_slug="bge-large"
        )

        service_context = ServiceContext.from_defaults(llm=self.myllm, embed_model=self.embed_model, chunk_size=256)
        set_global_service_context(service_context)

        self.indexes = {}

    def load_documents(self, user_id, directory):
        documents = SimpleDirectoryReader(directory).load_data()
        print(f"Loaded {len(documents)} document(s) for user {user_id}.")

        index = VectorStoreIndex.from_documents(documents, embed_model=self.embed_model)
        self.indexes[user_id] = index.as_query_engine(llm=self.myllm)

    def query(self, user_id, query_text):
        if user_id not in self.indexes:
            return "Documents not loaded. Please upload documents first."
        query_engine = self.indexes[user_id]
        response = query_engine.query(query_text)
        return response
