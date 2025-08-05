from app.__init__ import create_app


app = create_app()

app.env = "development"

if __name__ == "__main__":
    app.run(debug=True)