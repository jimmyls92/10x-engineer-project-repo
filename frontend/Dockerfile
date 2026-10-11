# Stage 1: build the static app with Node.
FROM node:24-alpine AS build

WORKDIR /app

# Copied before the code so the install layer is reused when only the code changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite writes the API address into the built files, so it is needed now, not at run time.
ARG VITE_API_BASE_URL
# Fail the build rather than ship an app that stops at start-up (src/api/client.js).
RUN test -n "$VITE_API_BASE_URL" || (echo "Build argument VITE_API_BASE_URL is required" && exit 1)
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: serve the built files with nginx; Node is not in the final image.
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
