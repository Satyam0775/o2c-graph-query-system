from fastapi import APIRouter
from app.api.routes import health, load_data, graph, node, query

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(load_data.router, tags=["Data"])
api_router.include_router(graph.router, tags=["Graph"])
api_router.include_router(node.router, tags=["Node"])
api_router.include_router(query.router, tags=["Query"])