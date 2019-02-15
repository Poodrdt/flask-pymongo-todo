LIST with list entrys
-create    POST   /lists/             name:str
-fetch one GET    /lists/<pk>
-fetch all GET    /lists/
-modify    PUT    /lists/<pk>         name:str
-delete    DELETE /lists/<pk>

ENTRY
create    POST   /api/v1/todo-list-entry/       parent_list:pk text:str due_date:date finished:bool
fetch one GET    /api/v1/todo-list-entry/<pk>
fetch all GET    /api/v1/todo-list-entry/
modify    PUT    /api/v1/todo-list-entry/<pk>   parent_list:pk text:str due_date:date finished:bool
delete    DELETE /api/v1/todo-list-entry/<pk>

