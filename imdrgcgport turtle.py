import turtle

def draw_map():
    screen = turtle.Screen()
    screen.setup(width=1000, height=600)
    screen.bgcolor("#2c3e50") # Deep ocean blue
    screen.title("High-Speed Turtle Projection")
    
    # POWER MOVE: Turn off animation for instant drawing
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    
    # 1. Draw Latitude/Longitude Grid
    t.pencolor("#34495e")
    for lat in range(-90, 91, 30):
        t.penup()
        t.goto(-400, lat * 3)
        t.pendown()
        t.goto(400, lat * 3)
    for lon in range(-180, 181, 30):
        t.penup()
        t.goto(lon * 2.2, -270)
        t.pendown()
        t.goto(lon * 2.2, 270)

    # 2. Draw Simplified World Silhouettes
    # Coordinates are (Longitude, Latitude) scaled for the screen
    landmasses = {
        "Americas": [(-100, 50), (-120, 70), (-60, 70), (-40, 50), (-40, 0), (-80, -50), (-40, -50), (-30, 0)],
        "Eurasia/Africa": [(0, 70), (140, 70), (160, 40), (100, 0), (120, -30), (20, -35), (-20, 0), (-10, 40)],
        "Australia": [(110, -15), (150, -15), (150, -40), (110, -40)],
        "Antarctica": [(-180, -80), (180, -80), (180, -90), (-180, -90)]
    }

    t.pensize(2)
    for name, points in landmasses.items():
        t.penup()
        t.pencolor("white")
        t.fillcolor("#27ae60") # Forest green
        
        # Scale and move to starting point
        t.goto(points[0][0] * 2.2, points[0][1] * 3)
        t.begin_fill()
        t.pendown()
        for x, y in points:
            t.goto(x * 2.2, y * 3)
        t.end_fill()
        
        # Label the mass
        t.penup()
        t.goto(points[0][0] * 2.2, (points[0][1] * 3) - 20)
        t.color("white")
        t.write(name, font=("Verdana", 10, "bold"))

    # Update the screen once at the very end
    screen.update()
    print("Map drawn in less than 1 second!")
    screen.exitonclick()

draw_map()