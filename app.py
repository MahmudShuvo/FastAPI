import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Load tasks from JSON file
def load_tasks():
    try:
        if not os.path.exists("data/tasks.json"):
            with open("data/tasks.json", "w") as f:
                json.dump([], f)
        with open("data/tasks.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        return []

# Save tasks to JSON file
def save_tasks(tasks):
    try:
        with open("data/tasks.json", "w") as f:
            json.dump(tasks, f)
    except Exception as e:
        logger.error(f"Error saving tasks: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        tasks = load_tasks()
        return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})
    except Exception as e:
        logger.error(f"Error in index: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

@app.post("/add", response_class=HTMLResponse)
async def add_task(request: Request, task: str = Form(...)):
    try:
        tasks = load_tasks()
        tasks.append({"task": task, "completed": False})
        save_tasks(tasks)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

@app.post("/complete/{task_index}", response_class=HTMLResponse)
async def complete_task(request: Request, task_index: int):
    try:
        tasks = load_tasks()
        tasks[task_index]["completed"] = True
        save_tasks(tasks)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

@app.post("/delete/{task_index}", response_class=HTMLResponse)
async def delete_task(request: Request, task_index: int):
    try:
        tasks = load_tasks()
        tasks.pop(task_index)
        save_tasks(tasks)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

@app.get("/edit/{task_index}", response_class=HTMLResponse)
async def edit_task(request: Request, task_index: int):
    try:
        tasks = load_tasks()
        task_to_edit = tasks[task_index]
        return templates.TemplateResponse("edit_task.html", {"request": request, "task_index": task_index, "task": task_to_edit})
    except Exception as e:
        logger.error(f"Error editing task: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

@app.post("/update/{task_index}", response_class=HTMLResponse)
async def update_task(request: Request, task_index: int, updated_task: str = Form(...)):
    try:
        tasks = load_tasks()
        tasks[task_index]["task"] = updated_task
        save_tasks(tasks)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)
