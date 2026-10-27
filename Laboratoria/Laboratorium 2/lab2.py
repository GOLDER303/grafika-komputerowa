#! /usr/bin/env python3

import random
import sys
from typing import Any

from glfw.GLFW import (
    glfwCreateWindow,
    glfwGetTime,
    glfwInit,
    glfwMakeContextCurrent,
    glfwSetFramebufferSizeCallback,
    glfwSwapBuffers,
    glfwSwapInterval,
    glfwTerminate,
    glfwWaitEvents,
    glfwWindowShouldClose,
)
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_TRIANGLES,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glEnd,
    glFlush,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glVertex2f,
    glViewport,
)

Vertex = tuple[float, float]
Color = tuple[float, float, float]

randomSeed = random.randint(0, 100)


def update_viewport(window: Any | None, width: int, height: int):
    if height == 0:
        height = 1

    if width == 0:
        width = 1

    aspectRatio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-100, 100, -100 / aspectRatio, 100 / aspectRatio, 1, -1)

    else:
        glOrtho(-100 * aspectRatio, 100 * aspectRatio, -100, 100, 1, -1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def startup():
    glClearColor(0.5, 0.5, 0.5, 1.0)
    update_viewport(None, 400, 400)


def shutdown():
    pass


def drawTriangle(
    vertex1: Vertex,
    vertex2: Vertex,
    vertex3: Vertex,
    color1: Color = (1.0, 0.0, 0.0),
    color2: Color = (0.0, 1.0, 0.0),
    color3: Color = (0.0, 0.0, 1.0),
):
    glBegin(GL_TRIANGLES)
    glColor3f(*color1)
    glVertex2f(*vertex1)
    glColor3f(*color2)
    glVertex2f(*vertex2)
    glColor3f(*color3)
    glVertex2f(*vertex3)
    glEnd()


def drawRectangle(
    x: float,
    y: float,
    width: float,
    height: float,
    random_colors: bool = False,
    d: float = 0.0,
):
    halfWidth, halfHeight = width / 2, height / 2
    corners = [
        (x - halfWidth, y - halfHeight),
        (x + halfWidth, y - halfHeight),
        (x + halfWidth, y + halfHeight),
        (x - halfWidth, y + halfHeight),
    ]

    vertices = [
        (
            cornerX + random.uniform(-d, d) * width,
            cornerY + random.uniform(-d, d) * height,
        )
        for cornerX, cornerY in corners
    ]

    colors = [(random.random(), random.random(), random.random()) for _ in corners]

    glBegin(GL_TRIANGLES)
    for i in (0, 1, 2, 0, 2, 3):
        if random_colors:
            glColor3f(*colors[i])
        glVertex2f(*vertices[i])
    glEnd()


def drawCarpet(x: float, y: float, width: float, height: float, level: int):
    if level == 0:
        drawRectangle(x, y, width, height)
        return

    for column in (-1, 0, 1):
        for row in (-1, 0, 1):
            if column == 0 and row == 0:
                continue
            drawCarpet(
                x + column * width / 3,
                y + row * height / 3,
                width / 3,
                height / 3,
                level - 1,
            )


def calculateMidpoint(v1: Vertex, v2: Vertex) -> Vertex:
    return ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2)


def drawSierpinskiTriangle(
    bottomLeft: Vertex, bottomRight: Vertex, top: Vertex, level: int
):
    if level == 0:
        drawTriangle(bottomLeft, bottomRight, top, (0, 0, 0), (0, 0, 0), (0, 0, 0))
        return

    leftMiddle: Vertex = calculateMidpoint(bottomLeft, top)
    rightMiddle: Vertex = calculateMidpoint(bottomRight, top)
    bottomMidle: Vertex = calculateMidpoint(bottomLeft, bottomRight)

    drawSierpinskiTriangle(bottomLeft, bottomMidle, leftMiddle, level - 1)
    drawSierpinskiTriangle(bottomMidle, bottomRight, rightMiddle, level - 1)
    drawSierpinskiTriangle(leftMiddle, rightMiddle, top, level - 1)


def render(time: float):
    glClear(GL_COLOR_BUFFER_BIT)

    # drawCarpet(0, 0, 200, 200, 5)
    drawSierpinskiTriangle((-90.0, -80.0), (90.0, -80.0), (0.0, 76.0), 5)

    glFlush()


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    _ = glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    startup()

    while not glfwWindowShouldClose(window):
        random.seed(randomSeed)
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwWaitEvents()
    shutdown()

    glfwTerminate()


if __name__ == "__main__":
    main()
