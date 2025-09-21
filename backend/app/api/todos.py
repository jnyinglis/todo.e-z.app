from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.schemas.todo import Todo as TodoSchema, TodoCreate, TodoUpdate

router = APIRouter()


@router.get("/", response_model=List[TodoSchema])
async def get_todos(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[TodoSchema]:
    """Get all todos for the current user"""
    result = await db.execute(
        select(Todo).where(Todo.user_id == current_user.id).order_by(Todo.created_at.desc())
    )
    todos = result.scalars().all()
    return [TodoSchema.model_validate(todo) for todo in todos]


@router.post("/", response_model=TodoSchema, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TodoSchema:
    """Create a new todo"""
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        completed=todo_data.completed,
        user_id=current_user.id
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return TodoSchema.model_validate(todo)


@router.get("/{todo_id}", response_model=TodoSchema)
async def get_todo(
    todo_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TodoSchema:
    """Get a specific todo by ID"""
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return TodoSchema.model_validate(todo)


@router.put("/{todo_id}", response_model=TodoSchema)
async def update_todo(
    todo_id: UUID,
    todo_data: TodoUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TodoSchema:
    """Update a todo"""
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    # Update only provided fields
    update_data = todo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    await db.commit()
    await db.refresh(todo)
    return TodoSchema.model_validate(todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a todo"""
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    await db.delete(todo)
    await db.commit()


@router.patch("/{todo_id}/toggle", response_model=TodoSchema)
async def toggle_todo_completion(
    todo_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TodoSchema:
    """Toggle the completion status of a todo"""
    result = await db.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    todo.completed = not todo.completed
    await db.commit()
    await db.refresh(todo)
    return TodoSchema.model_validate(todo)