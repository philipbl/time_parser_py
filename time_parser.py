from operator import add, sub

import click
import inflect
from lark import Lark
from loguru import logger

p = inflect.engine()
operations = {"+": add, "-": sub}
OUTPUT = "hour"

def parse_rel_time(token):
    number, description = token.children
    
    if number.type == "INT":
        number = int(number)
    elif number.type == "DECIMAL":
        number = float(number)
    else:
        raise SyntaxError("Unknown number type: %s" % number.type)
        
    if description.data == "hour":
        number *= 60
    elif description.data == "min":
        pass
    else:
        raise SyntaxError("Unknown time description: %s" % description.data)

    return number

def parse_abs_time(token):
    if len(token.children) == 3:
        hour, minute, day = token.children
    elif len(token.children) == 2:
        hour, day = token.children
        minute = 0
    else:
        raise SyntaxError("Unknown time format: %s" % token.children)

    hour = int(hour)
    minute = int(minute)

    total_minutes = hour * 60 + minute

    if day.data == "am":
        pass
    elif day.data == "pm":
        if hour != 12:
            total_minutes += 12 * 60
    else:
        raise SyntaxError("Unknown time format: %s" % day.data)

    return total_minutes

def run(t):
    # t is always a statement
    first, *rest = t.children
    
    if first.data == "abs_statement":
        abs_statement = first
        first_time, second_time = abs_statement.children
        first_time_minutes = parse_abs_time(first_time)
        second_time_minutes = parse_abs_time(second_time)

        minutes = second_time_minutes - first_time_minutes
        
        if minutes < 0:
            # We rolled over to different day
            minutes += 24 * 60

    if first.data == "rel_time":
        rel_time = first
        minutes = parse_rel_time(rel_time)

    if len(rest) == 0:
        return minutes
    else:
        operator = operations[rest[0]]
        return operator(minutes, run(rest[1]))


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--output", type=click.Choice(["hour", "minute", "both"], case_sensitive=False), default="both")
def cli(debug, output):
    global OUTPUT

    if not debug:
        logger.remove()

    OUTPUT = output

@cli.command()
@click.argument("input", nargs=-1)
def command(input):
    parse(" ".join(input))

@cli.command()
@click.argument("input", type=click.File("r"))
def file(input):
    parse(input.read())


def parse(input):
    with open("grammar.txt") as f:
        grammar = f.read()

    parser = Lark(grammar)

    parse_tree = parser.parse(input)

    logger.debug(parse_tree.pretty())
    logger.debug(parse_tree)

    minutes = run(parse_tree.children[0])


    if OUTPUT == "hour":
        # Cast to int if there is no remainder
        if minutes % 60 == 0:
            hours = int(minutes / 60)
        else:
            hours = round(minutes / 60, 2)
        print(hours, p.plural("hour", hours))

    elif OUTPUT == "minute":
        print(minutes, p.plural("minute", minutes))

    elif OUTPUT == "both":
        hours = int(minutes / 60)
        minutes = minutes % 60

        if minutes == 0:
            print(hours, p.plural("hour", hours))
        elif hours == 0:
            print(minutes, p.plural("minute", minutes))
        else:
            print(hours, p.plural("hour", hours), minutes, p.plural("minute", minutes))



if __name__ == "__main__":
    cli()
