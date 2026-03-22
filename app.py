import streamlit as st
import json
from crawler import crawl_url
from search_fulltext import search_fulltext

def load_pages():
    """JSONファイルからページリストを取得（空ファイル対応済み）"""
    try:
        with open("pages.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_pages(pages):
    """ページリストをJSONに保存"""
    with open("pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)


st.set_page_config(page_title="Tech0-Search")
st.title("Tech0-Search ver2")
st.caption('PROJECT 0 検索エンジン')


pages = load_pages()

tab1, tab2, tab3, tab4= st.tabs(['🔍検索', '🚙自動登録','🍎手動登録', '📝データ一覧'])

with tab1:
    pages = load_pages()
    query = st.text_input('検索キーワードを入力（例：DX）')
    if query:
        results = search_fulltext(query, pages)
        st.success(f"検索結果: {len(results)} 件")
        for page in results:
            with st.container(border=True):
                st.markdown(f"### [{page['title']}]({page['url']})")

                col1, col2, col3 = st.columns(3)
                col1.caption(f"マッチ度: {page.get('match_count', 0)}")
                col2.caption(f"カテゴリ: {page.get('category', '未分類')}")
                
                st.write("キーワード:", "、".join(page['keywords']))
                st.write(page["preview"][:120])
                

with tab2:
    st.write("🚙単体クロール")
    url_single = st.text_input("取得したいURLを入力", key="single_url")
    run_single = st.button('実行', key="run_single", type="primary")

    if run_single and url_single:
        result = crawl_url(url_single)
        if result["crawl_status"] == "success":
            pages = load_pages()
            pages.append(result)
            save_pages(pages)
            st.success("登録完了")
            st.rerun()
        else:
            st.error("取得失敗")

    st.write("🛫一括クロール")
    url_multi = st.text_area("取得したいURLを入力（１行に１URL）", key="multi_url")
    run_multi = st.button('実行', key="run_multi", type="primary")

    if run_multi and url_multi:
        urls = url_multi.split("\n")
        success_count = 0

        for u in urls:
           result = crawl_url(u.strip())
           if result["crawl_status"] == "success":
                pages.append(result)
                success_count += 1

        save_pages(pages)

        if success_count > 0:
            st.success(f"{success_count}件登録完了")
            st.rerun()
        else:
            st.error("取得失敗")

with tab3:
    with st.form('register_form'):
        #入力フィールド
        title = st.text_input('タイトル')
        url = st.text_input('URL')
        description = st.text_input('説明文')
        author = st.text_input('作成者')
        category = st.text_input('カテゴリ')
        keywords = st.text_input('キーワード（カンマ区切り）')
                         
        submitted = st.form_submit_button('登録する')
   
    if submitted:
        pages = load_pages()
        new_page = {
            "title": title,
            "url": url,
            "description": description,
            "author": author,
            "category": category,
            "keywords": keywords.split(",")
        }

        pages.append(new_page)
        save_pages(pages)
        st.cache_data.clear()
        st.rerun()
            
with tab4:
    pages = load_pages()
    st.write(f"現在の登録件数: {len(pages)} 件")

    for page in pages:
        with st.expander(page['title']):
            st.write("URL:", page.get('url', '-'))
            st.write("説明:", page.get('description', '-'))
            st.write("作成者:",page.get('author', '-'))
            st.write("カテゴリ:", page.get('category', '未分類'))
            st.write("キーワード:", ", ".join(page.get('keywords', [])))
            st.write("本文:", page.get('full_text'[:120], '-')[:200])