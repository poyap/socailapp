# socailapp
Social app using django
In this django app we use jquery in order to be able to bookmark images from other websites. 
we integrated django with ajax to add like/unlike and follow/unfollow functionallity without having to refresh the page. also with signals we can notify other apps to change number of likes when an images gets likes.
And last with redis(key/value database) we can count total like and rank the most viewed images without overheading the actuall database.
