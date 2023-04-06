docker build -t chatbot . || exit

docker run -itd --name telegram_chatbot --network host chatbot || exit