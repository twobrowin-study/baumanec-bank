all: firms.pdf clients.pdf

firms.fodg:
	TEMPLATE_FILENAME='firms.template.fodg' OUTPUT_FILENAME='firms.fodg' TG_BOT_NAME='BauBankAccountBot' CONDITIONS='id <= 104' python main.py

firms.pdf: firms.fodg
	libreoffice --convert-to pdf firms.fodg

clients.fodg:
	TEMPLATE_FILENAME='clients.template.fodg' OUTPUT_FILENAME='clients.fodg' TG_BOT_NAME='BauBankClientBot' CONDITIONS='id > 104 and id <= 496' python main.py

clients.pdf: clients.fodg
	libreoffice --convert-to pdf clients.fodg

clean:
	@rm firms.fodg clients.fodg firms.pdf clients.pdf