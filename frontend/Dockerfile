# Stage 1: Build the app
FROM node:18 as build

WORKDIR /app

# Copy the package.json and package-lock.json to install dependencies
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY frontend/. .

# Build the app
# RUN npm run build

# FROM nginx:alpine

# COPY --from=build /dist /usr/share/nginx/html

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]