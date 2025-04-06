import click
from assistant import generate_query
from database import run_query

@click.command()
def start():
    click.secho("Movie Database Assistant. Type 'exit' to quit.", bold=True)
    while True:
        try:
            user_input = click.prompt('> ', prompt_suffix='')
            if _exit_cmd(user_input):
                break

            query = generate_query(user_input)
            click.secho(query, fg="cyan", italic=True)
            result = run_query(query)
            click.echo(result)

        except Exception as e:
            click.secho(f"Error: {e}", fg="red")


def _exit_cmd(user_input):
    if user_input.lower() in ['exit', 'quit']:
        click.secho("Bye...", bold=True)
        return True
    return False


if __name__ == '__main__':
    start()
