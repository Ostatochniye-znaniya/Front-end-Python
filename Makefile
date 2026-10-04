dev-up-d:
	docker compose -f docker-compose.dev.yml up -d --build

dev-up:
	docker compose -f docker-compose.dev.yml up --build

dev-down:
	docker compose -f docker-compose.dev.yml down

prod-up-d:
	docker compose -f docker-compose.prod.yml up -d --build

prod-up:
	docker compose -f docker-compose.prod.yml up --build

prod-down:
	docker compose -f docker-compose.prod.yml down
