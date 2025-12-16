from mrkdwn_analysis import MarkdownAnalyzer

analyzer = MarkdownAnalyzer("НИР_Косов Андрей Сергеевич.md")
headers = analyzer.identify_headers()
paragraphs = analyzer.identify_paragraphs()
links = analyzer.identify_links()
tables = analyzer.identify_tables()

print(f"Headers found: {headers}")
print(f"Paragraphs found: {paragraphs}")
print(f"Links found: {links}")
print(f"Tables found: {tables}")
