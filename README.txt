project_title = 'teaching_app'

Objective:
The app will use help of LLM and help user to know about different positions available at amazon depending upon his/her qualifications.

Constraints:
- As LLM-GPT- is used for generating conversation from backend, some conversations might not be up to the point

Backend:
- Languages: Python
- Tools/Frameworks: Django
- Packages downloaded: Djongo(connects Django with MongoDB)
- Database: MongoDB

Frontend:
- Languages: JavaScript
- Tools/Frameworks: HTML, CSS, ReactJS
- Packages downloaded: react-router-dom, react-bootstrap, react-redux, @reduxjs/toolkit


Architecture:
            Authentication: Login and signup will be done using "MERN STRACK" as microservice. 
                                    Follow this link for more info: https://github.com/aayush6200/mern-auth

            Authorization:For Authorization and accessing the app, all the associates will be manually registered on Django
                          Database. So when user registers using his email/password, if he is not in django database, he will
                          not be able to access app
    
            DB for authorization and authorization(SQL):
                                database will register all users 




