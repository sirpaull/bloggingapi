from main import create_app

app = create_app()

# Entry point for running the app
if __name__ == '__main__':
   
    app.run(debug=True)
