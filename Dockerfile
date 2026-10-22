FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# python3-tk  -> tkinter for the game
# xvfb        -> virtual screen (browser mode)
# x11vnc + novnc + websockify -> streams that screen to your web browser
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-tk xvfb x11vnc novnc websockify \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ludo.py entrypoint.sh /app/
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 6080
ENTRYPOINT ["/app/entrypoint.sh"]
