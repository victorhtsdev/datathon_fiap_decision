# Dockerfile para Frontend React + Vite
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
