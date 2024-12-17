from fasthtml.common import *

# Initialize the app, routes, and the Todo model with the database
app, rt,todos, Todo = fast_app('data/todos.db', id=int, title=str, description=str, done=bool, pk='id')

# Function to display a single Todo item in the list
def TodoRow(todo):
    return Li(
        H6(todo.title, style="display: inline; "),
        A(' edit', href=f'/edit/{todo.id}', style="display: inline; margin-left: 15px"),
        Span(todo.description, style="font-size: smaller; display: block; margin-top: 5px;"),
        id=f'todo-{todo.id}'
    )

# Function to display a single done Todo item in the list
def Tododone(todo):
    return Li(
        H6(todo.title, style="display: inline;"),
        A(' edit', href=f'/editdone/{todo.id}',style = "display:inline;margin: 15px"),
        id=f'todo-{todo.id}'
    )

# Function to check if a Todo is active (not done)
def is_active(todo):
    return not todo.done

# Function to check if a Todo is done
def is_done(todo):
    return todo.done

# Home route: displays both active and done Todos separately
@app.get("/")
def home():
    # Form to add a new Todo
    add = Form(
        Group(
            Group(
                Input(name="title", placeholder="New Todo",required = True),
                Input(name="description", placeholder="Add description",style="font-size:smaller"),
                style="display: flex; flex-direction: column; align-items: flex-start; gap: 10px;"
            ),
            Button("Add", style="align-self: center; margin-left:15px ;"),
            style="display: flex; justify-content: space-between; align-items: center; width: 98%;"
        ),
        action="/", method='post'
    )
    # Create a list of active Todos (not done)
    active_todos = Ul(*map(TodoRow, filter(is_active, todos())), id='active-todo-list')

    # Create a list of done Todos (marked as done)
    done_todos = Ul(*map(Tododone, filter(is_done, todos())), id='done-todo-list')

    # Card for displaying the two lists and the "Add Todo" form
    card = Card(
        H3("Todos"),  # Title for the active Todos list
        active_todos,  # Display active Todos list
        H3("Done"),  # Title for the done Todos list
        done_todos,  # Display done Todos list
        header=add,
        footer=Div(id='current-todo')
    )

    # Return the page with the Todo lists
    return Titled('Todo list', card)

# Route to handle adding a new Todo
@app.post("/")
def add_todo(todo: Todo):
    todos.insert(todo)
    return home()

# Route to handle updating a Todo
@app.post("/update")
def update_todo(todo: Todo):
    todos.update(todo)
    return home()

# Route to handle removing a Todo
@app.get("/remove")
def remove_todo(id: int):
    todos.delete(id)
    return home()

# Route to handle editing a Todo
@app.get("/edit/{id}")
def edit_todo(id: int):
    res = Form(
        Button("Save",role="button", style="margin-bottom: 15px;"),
        Group(
            H6("Title", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="title"),
            style="display: flex; align-items: center; gap: 10px;"
            ),
        Group(
            H6("Description", style="margin-right: 10px; min-width: 60px;white-space: nowrap; text-align: left;"),
            Input(id="description", placeholder="Add Description"),
            style="display: flex; align-items: center; gap: 10px;"
            ),
        CheckboxX(id="done", label='done'),
        Hidden(id="id"),
        A('Delete',href=f'/remove?id={id}',role="button",onclick="return confirm('Are you sure you want to delete this Todo?');"),
        A('Back', href='/', role="button",style="margin:15px"),action="/update", id="edit", method='post'
    )
    frm = fill_form(res, todos[id])
    return Titled('Edit Todo', frm)

# Route to handle editing a Tododone (to mark it as undone)
@app.get("/editdone/{id}")
def edit_todo_done(id: int):
    res = Form(
            Button("Save",style = "margin-bottom:10px"),
        Hidden(id="id"),
        CheckboxX(id="done", label='not done' ),  # Uncheck to mark as undone
        A('Delete',href=f'/remove?id={id}',role="button",onclick="return confirm('Are you sure you want to delete this Todo?');"),

        A('Back', href='/', role="button",style="margin:15px"),action="/update", id="edit", method='post'
    )
    frm = fill_form(res, todos[id])
    return Titled('Edit Tododone', frm)

# Start the server to handle requests
serve()
