import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import type { Todo, TodoCreate } from '../services/api';

interface TodoItemProps {
  todo: Todo;
  onToggle: (todoId: string) => void;
  onDelete: (todoId: string) => void;
  onEdit: (todoId: string, newTitle: string) => void;
}

const TodoItem: React.FC<TodoItemProps> = ({ todo, onToggle, onDelete, onEdit }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);

  const handleEdit = () => {
    if (isEditing && editTitle.trim() !== todo.title) {
      onEdit(todo.id, editTitle.trim());
    }
    setIsEditing(!isEditing);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleEdit();
    } else if (e.key === 'Escape') {
      setEditTitle(todo.title);
      setIsEditing(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: '0.75rem',
      borderBottom: '1px solid #e9ecef',
      backgroundColor: todo.completed ? '#f8f9fa' : '#ffffff'
    }}>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
        style={{ marginRight: '0.75rem', transform: 'scale(1.2)' }}
      />

      {isEditing ? (
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onBlur={handleEdit}
          onKeyDown={handleKeyPress}
          autoFocus
          style={{
            flex: 1,
            padding: '0.25rem',
            border: '1px solid #007bff',
            borderRadius: '3px',
            fontSize: '1rem'
          }}
        />
      ) : (
        <span
          style={{
            flex: 1,
            textDecoration: todo.completed ? 'line-through' : 'none',
            color: todo.completed ? '#6c757d' : '#000',
            cursor: 'pointer'
          }}
          onClick={() => setIsEditing(true)}
        >
          {todo.title}
        </span>
      )}

      {todo.description && (
        <span style={{
          fontSize: '0.8rem',
          color: '#6c757d',
          marginLeft: '0.5rem',
          marginRight: '0.5rem'
        }}>
          {todo.description}
        </span>
      )}

      <button
        onClick={() => setIsEditing(!isEditing)}
        style={{
          marginLeft: '0.5rem',
          marginRight: '0.25rem',
          padding: '0.25rem 0.5rem',
          backgroundColor: '#17a2b8',
          color: 'white',
          border: 'none',
          borderRadius: '3px',
          cursor: 'pointer',
          fontSize: '0.8rem'
        }}
        title="Edit"
      >
        ✏️
      </button>

      <button
        onClick={() => onDelete(todo.id)}
        style={{
          marginLeft: '0.25rem',
          padding: '0.25rem 0.5rem',
          backgroundColor: '#dc3545',
          color: 'white',
          border: 'none',
          borderRadius: '3px',
          cursor: 'pointer',
          fontSize: '0.8rem'
        }}
        title="Delete"
      >
        🗑️
      </button>
    </div>
  );
};

interface TodoListProps {}

const TodoList: React.FC<TodoListProps> = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTodos = async () => {
    try {
      setLoading(true);
      const todosData = await apiService.getTodos();
      setTodos(todosData);
      setError(null);
    } catch (err) {
      setError('Failed to load todos');
      console.error('Error loading todos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTodos();
  }, []);

  const handleCreateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;

    try {
      const todoData: TodoCreate = {
        title: newTodoTitle.trim(),
        description: newTodoDescription.trim() || undefined,
        completed: false
      };

      const newTodo = await apiService.createTodo(todoData);
      setTodos([newTodo, ...todos]);
      setNewTodoTitle('');
      setNewTodoDescription('');
    } catch (err) {
      setError('Failed to create todo');
      console.error('Error creating todo:', err);
    }
  };

  const handleToggleTodo = async (todoId: string) => {
    try {
      const updatedTodo = await apiService.toggleTodoCompletion(todoId);
      setTodos(todos.map(todo =>
        todo.id === todoId ? updatedTodo : todo
      ));
    } catch (err) {
      setError('Failed to update todo');
      console.error('Error toggling todo:', err);
    }
  };

  const handleDeleteTodo = async (todoId: string) => {
    if (!confirm('Are you sure you want to delete this todo?')) return;

    try {
      await apiService.deleteTodo(todoId);
      setTodos(todos.filter(todo => todo.id !== todoId));
    } catch (err) {
      setError('Failed to delete todo');
      console.error('Error deleting todo:', err);
    }
  };

  const handleEditTodo = async (todoId: string, newTitle: string) => {
    try {
      const updatedTodo = await apiService.updateTodo(todoId, { title: newTitle });
      setTodos(todos.map(todo =>
        todo.id === todoId ? updatedTodo : todo
      ));
    } catch (err) {
      setError('Failed to update todo');
      console.error('Error updating todo:', err);
    }
  };

  const completedCount = todos.filter(todo => todo.completed).length;
  const totalCount = todos.length;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading todos...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '1rem' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>My Todos</h1>

      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          padding: '0.75rem',
          borderRadius: '4px',
          marginBottom: '1rem',
          border: '1px solid #f5c6cb'
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleCreateTodo} style={{ marginBottom: '2rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Add a new todo..."
            value={newTodoTitle}
            onChange={(e) => setNewTodoTitle(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              border: '1px solid #dee2e6',
              borderRadius: '4px'
            }}
            required
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Description (optional)"
            value={newTodoDescription}
            onChange={(e) => setNewTodoDescription(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              fontSize: '0.9rem',
              border: '1px solid #dee2e6',
              borderRadius: '4px'
            }}
          />
        </div>
        <button
          type="submit"
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            cursor: 'pointer'
          }}
        >
          Add Todo
        </button>
      </form>

      <div style={{ marginBottom: '1rem', textAlign: 'center', color: '#6c757d' }}>
        {completedCount} of {totalCount} completed
      </div>

      <div style={{
        border: '1px solid #dee2e6',
        borderRadius: '4px',
        backgroundColor: '#ffffff'
      }}>
        {todos.length === 0 ? (
          <div style={{
            padding: '2rem',
            textAlign: 'center',
            color: '#6c757d'
          }}>
            No todos yet. Create your first todo above!
          </div>
        ) : (
          todos.map(todo => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onToggle={handleToggleTodo}
              onDelete={handleDeleteTodo}
              onEdit={handleEditTodo}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default TodoList;