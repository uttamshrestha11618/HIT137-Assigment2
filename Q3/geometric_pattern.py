import turtle

# one edge with inward indentation (recursive)
def edge(L, k):
    if k == 0:
        turtle.forward(L)
        return
    s = L / 3
    edge(s, k - 1)
    turtle.left(60)
    edge(s, k - 1)
    turtle.right(120)
    edge(s, k - 1)
    turtle.left(60)
    edge(s, k - 1)

# full polygon of fractal edges
def shape(n, L, k):
    turn = 360 / n
    for _ in range(n):
        edge(L, k)
        turtle.left(turn)

# basic inputs (no validation)
n = int(input("Enter the number of sides: "))
L = float(input("Enter the side length: "))
k = int(input("Enter the recursion depth: "))

# simple setup and rough centering
turtle.setup(1000, 800)
turtle.speed(0)
turtle.pensize(2)
turtle.hideturtle()
turtle.tracer(False)
turtle.penup()
turtle.goto(-L / 2, -L / 3)
turtle.setheading(0)
turtle.pendown()

shape(n, L, k)

turtle.update()
turtle.done()