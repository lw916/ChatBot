docker build -t chatbot . || exit

docker run -itd --name telegram_chatbot chatbot || exit