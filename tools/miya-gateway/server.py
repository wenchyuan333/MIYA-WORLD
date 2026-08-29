from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tools.miya_gateway.registry import list_functions, get_function
from tools.miya_gateway.executor import invoke
import uvicorn

app = FastAPI(title="MIYA Gateway")

class InvokeReq(BaseModel):
    name: str
    args: dict = {}
    caller: str = "api"

@app.get("/functions")
def functions():
    return list_functions()

@app.post("/invoke")
def call(req: InvokeReq):
    fn = get_function(req.name)
    if not fn:
        raise HTTPException(status_code=404, detail="function not found")
    return invoke(req.name, req.args, caller=req.caller)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8787)
