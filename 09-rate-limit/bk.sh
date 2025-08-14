


[ $# -eq 0 ] && echo Need comment && exit


sch_bk backend/app/main.py "$@"
sch_bk frontend/chatbot.js "$@"
sch_bk frontend/style.css "$@"
sch_bk frontend/index.html "$@"

