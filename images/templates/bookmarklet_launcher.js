(function(){
    if (window.mybookmarklet !== undefined){
        mybookmarklet();
    }
    else{
        document.body.appendChild(document.createElement('script')).src='https://localhost:9000/static/js/bookmarklet.js?r=' + Math.floor(Math.random()*999);
    }
})();
