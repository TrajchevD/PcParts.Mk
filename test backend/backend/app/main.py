# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.products_router import router as products_router
# from app.image_proxy import router as image_proxy_router
# from app.alerts_router import router as alerts_router
# from app.routers.alerts_router import router as alerts_router
# from app.routers.notifications_router import router as notifications_router
# from app.auth.auth_router import router as auth_router

# app = FastAPI(title="Price Compare API", version="1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(products_router)
# app.include_router(image_proxy_router)
# app.include_router(alerts_router)
# app.include_router(alerts_router)
# app.include_router(notifications_router)
# app.include_router(auth_router)

# @app.get("/")
# def root():
#     return {"status": "ok", "message": "API is running"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.products_router import router as products_router
from app.image_proxy import router as image_proxy_router

from app.routers.alerts_router import router as alerts_router
from app.routers.notifications_router import router as notifications_router
from app.auth.auth_router import router as auth_router

# ✅ ADD THIS
from app.routers.pc_builder import router as pc_builder_router
from app.routers.cpu_products import router as cpu_products_router
from app.routers.gpu_products import router as gpu_products_router
from app.routers.mb_products import router as mb_products_router
from app.routers.ram_products import router as ram_products_router
from app.routers.storage_products import router as storage_products_router
from app.routers.pc_builder_v2 import router as pc_builder_v2_router
from app.routers import pc_compare
from app.routers.recommendation import router as recommendation_router


app = FastAPI(title="Price Compare API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(image_proxy_router)
app.include_router(alerts_router)
app.include_router(notifications_router)
app.include_router(auth_router)
app.include_router(pc_compare.router)
# ✅ ADD THIS
app.include_router(pc_builder_router)
app.include_router(cpu_products_router)
app.include_router(gpu_products_router)
app.include_router(mb_products_router)
app.include_router(ram_products_router)
app.include_router(storage_products_router)
app.include_router(pc_builder_v2_router)
app.include_router(recommendation_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}
