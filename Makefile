.PHONY: dev build up down logs test seed migrate

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=100 | cat

seed:
	docker compose run --rm backend python -m app.seed.seed

migrate:
	docker compose run --rm backend alembic upgrade head

test:
	docker compose run --rm backend pytest -q
