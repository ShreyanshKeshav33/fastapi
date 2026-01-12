from typing import Optional
from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

app= FastAPI()

# python -m venv proj
# proj\Scripts\activate.bat

# for running - uvicorn app.main:app --reload


#Create the database tables
models.Base.metadata.create_all(bind=engine) #creates the tables in the database


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
   #rating: Optional[int] = None #optional field, what is none here? means it can be null, so whenever we use optional field we have to define it as none
   
    
my_posts=[{"title":"title of post 1","content":"content of post 1","id":1},
          {"title":"favorite foods","content":"i like pizza","id":2}]    

while True:
    try:
        conn= psycopg2.connect(host='localhost', database='postgres', user='postgres', password='supersetu', cursor_factory=RealDictCursor)
        cursor= conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(5)


@app.get("/")
def root():
    return {"Hello, World!"} 

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)): #db session is passed to the function using dependency injection, what does dession do here? ans- it provides a database session to the function, what does depends do here? ans- it is used to declare dependencies for the function, which means that the function will receive the database session as an argument, how is this dependency injected? ans- it is injected by FastAPI when the function is called which means that FastAPI will call the get_db function to get a database session and pass it to the test_posts function
    return {"status": "success"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""") #why 3""" here? ans- it is used for multi-line strings in python
    posts=cursor.fetchall()
    print(posts)
    return {"data": posts}



@app.post("/posts", status_code=status.HTTP_201_CREATED) #201 is for created
def create_posts(payLoad: Post): #extracts fields from the body of the request
    # print(payLoad)
    # print(payLoad.model_dump()) #.model_dump() method converts pydantic model to dictionary
    
    # payLoad_dict= payLoad.model_dump()
    # payLoad_dict['id']= randrange(0,1000000)
    # my_posts.append(payLoad_dict)
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", #whats returnin * here? ans- it returns the inserted row
                   (payLoad.title, payLoad.content, payLoad.published))
    new_post= cursor.fetchone()
    conn.commit() #to save the changes to the database
    return {"data":"post created", "post": new_post}

#path order matters tgat is why we put latest before {id}
@app.get("/posts/latest")
def get_latest_post():
    latest_post= my_posts[-1]
    return {"latest_post": latest_post}

#retrieving one single post
@app.get("/posts/{id}")

def get_post(id: int, response: Response):
    
    cursor.execute("""SELECT * FROM posts WHERE id= %s""", (id,)) #why (str(id),) with comma? ans- to make it a tuple, why to make a tuple? ans- because the execute method expects a tuple for the parameters
    test_post= cursor.fetchone() 
    print(test_post)
    for post in my_posts: #is post a diiferent variable here? ans- yes, it is a different variable that iterates through my_posts list
        if post['id'] == id:
            return {"post_detail": post}
    #response.status_code=404
    #return {"message": f"post with id: {id} was not found"}
    raise HTTPException(status_code=404, detail= f"post with id: {id} was not found")

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)

def delete_post(id: int):
    
    cursor.execute("""DELETE FROM posts WHERE id= %s RETURNING *""", (id,))
    deleted_post= cursor.fetchone()
    print(deleted_post)
    conn.commit()
    
    #for database deletion
    if not deleted_post:  # If no post was deleted (id doesn't exist)
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    #this is for my_posts list deletion
    # for index, post in enumerate(my_posts): #is post a diiferent variable here? ans- yes, it is a different variable that iterates through my_posts list and what is index here? ans- index is the position of the post in the my_posts list, and what is enumerate here? ans- enumerate is a built-in function that adds a counter to an iterable and returns it as an enumerate object
    #     if post['id'] == id:
    #         my_posts.pop(index) #pop method removes the element at the specified position
    #         return {"message": f"post with id: {id} was deleted"}
    # raise HTTPException(status_code=404, detail= f"post with id: {id} was not found")

#updating a post
@app.put("/posts/{id}")
def update_post(id: int, payLoad: Post):
    
    cursor.execute("""UPDATE posts SET title= %s, content= %s, published= %s WHERE id= %s RETURNING *""",
                   (payLoad.title, payLoad.content, payLoad.published, id))
    updated_post = cursor.fetchone()
    print(updated_post)
    conn.commit()
    
    #for database update
    if not updated_post:  # If no post was updated (id doesn't exist)
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    
    return {"data": updated_post}
    
    
    #this is for my_posts list update
    # for index, post in enumerate(my_posts):
    #     if post['id'] == id:
    #         my_posts[index]= payLoad.model_dump()
    #         my_posts[index]['id']= id
    #         return {"message": f"post with id: {id} was updated", "post": my_posts[index]}
    # raise HTTPException(status_code=404, detail= f"post with id: {id} was not found")