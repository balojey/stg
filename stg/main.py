from stg import app

def main() -> None:
    app.run(debug=False, use_reloader=True)

main()