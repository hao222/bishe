#-*-coding:utf-8-*-

def show_message(msg,url):
    str = '<script>alert("'+msg+'");location.href="'+url+'"</script>'
    return str