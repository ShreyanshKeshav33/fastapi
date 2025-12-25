from typing import Optional
from fastapi import FastAPI, Response, HTTPException, status
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app= FastAPI()

# python -m venv proj
# proj\Scripts\activate.bat

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None #optional field, what is none here? means it can be null, so whenever we use optional field we have to define it as none
    
my_posts=[{"title":"title of post 1","content":"content of post 1","id":1},
          {"title":"favorite foods","content":"i like pizza","id":2}]    

@app.get("/")
def root():
    return {"Hello, World!"} 

@app.get("/posts")
def get_posts():
    return {"data": my_posts}



@app.post("/posts", status_code=status.HTTP_201_CREATED) #201 is for created
def create_posts(payLoad: Post): #extracts fields from the body of the request
    print(payLoad)
    print(payLoad.model_dump()) #.model_dump() method converts pydantic model to dictionary
    
    payLoad_dict= payLoad.model_dump()
    payLoad_dict['id']= randrange(0,1000000)
    my_posts.append(payLoad_dict)
    return {"data":"post created", "post": payLoad_dict}

#path order matters tgat is why we put latest before {id}
@app.get("/posts/latest")
def get_latest_post():
    latest_post= my_posts[-1]
    return {"latest_post": latest_post}

#retrieving one single post
@app.get("/posts/{id}")

def get_post(id: int, response: Response):
    for post in my_posts: #is post a diiferent variable here? ans- yes, it is a different variable that iterates through my_posts list
        if post['id'] == id:
            return {"post_detail": post}
    #response.status_code=404
    #return {"message": f"post with id: {id} was not found"}
    raise HTTPException(status_code=404, detail= f"post with id: {id} was not found")

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)

def delete_post(id: int):
    for index, post in enumerate(my_posts): #is post a diiferent variable here? ans- yes, it is a different variable that iterates through my_posts list and what is index here? ans- index is the position of the post in the my_posts list, and what is enumerate here? ans- enumerate is a built-in function that adds a counter to an iterable and returns it as an enumerate object
        if post['id'] == id:
            my_posts.pop(index) #pop method removes the element at the specified position
            return {"message": f"post with id: {id} was deleted"}
    raise HTTPException(status_code=404, detail= f"post with id: {id} was not found")

#updating a post
@app.put("/posts/{id}")
def update_post(id: int, payLoad: Post):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            my_posts[index]= payLoad.model_dump()
            my_posts[index]['id']= id
            return {"message": f"post with id: {id} was updated", "post": my_posts[index]}
    raise HTTPException(status_code=404, detail= f"post with id: {id} was not found")