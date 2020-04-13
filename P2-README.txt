########## HOW TO RUN ############

Run the following commands in terminal:

foreman start -m post=3,vote=3,user=3,msg=3

ulimit -n 8192 && caddy

######## CURL COMMANDS ###########

##### USER API ######
-Create a new user
curl -i -X POST -H 'Content-Type:application/json' -d '{"username":"axel","email":"axel@animalcrossing.com"}' http://localhost:2015/users/register

-Update user's email
curl -i -X PUT -H 'Content-Type:application/json' -d '{"username":"axel", "email":"newAxel@animalcrossing.com"}' http://localhost:2015/users/update_email

-Add karma to user
curl -i -X PUT -H 'Content-Type:application/json' -d '{"username":"axel"}' http://localhost:2015/users/add_karma;

-Remove karma from user
curl -i -X PUT -H 'Content-Type:application/json' -d '{"username":"axel"}' http://localhost:2015/users/remove_karma

-Delete a user
curl -i -X DELETE http://localhost:2015/users/delete?username=axel;


###### MESSAGE API #####
-Send a message
curl -i -X POST -H 'Content-Type:application/json' -d '{"user_from":"ilovedog", "user_to":"ilovecat", "msg_content":"I think dogs are better", "msg_flag":"facts"}' http://localhost:2015/messages/send;


-Delete a message
curl -i -X DELETE http://localhost:2015/messages/delete?msg_id=3;

-Favorite a message
curl -i -X POST -H 'Content-Type:application/json' http://localhost:2015/messages/favorite?msg_id=3;
