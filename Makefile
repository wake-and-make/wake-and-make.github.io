.PHONY: publish

publish:
	git checkout main
	git pull origin main
	git checkout publish
	git rebase main
	git push origin publish
	git checkout main
