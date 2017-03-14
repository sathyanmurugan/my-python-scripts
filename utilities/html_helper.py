import io
import pandas as pd
from bs4 import BeautifulSoup

def is_html(string):
    """ Returns True if BeautifulSoup finds a html tag in string """
    return bool(BeautifulSoup(string, 'html.parser').find())

def get_html_paragraph(string):
    """ Wraps string into HTML paragraph. If string is already HTML, html, head, body tags are
        removed. Otherwise, line breaks are replaced with <br/> tags to get correct layout in HTML.
    """
    # Set up new HTML
    soup = BeautifulSoup('', 'html.parser')
    # Add paragraph tag
    paragraph = soup.new_tag('p')
    # Read string as HTML
    html = BeautifulSoup(string, 'html.parser')
    # If string is HTML, clean it and append it to paragraph
    if html.find():
        # Remove html tag if present
        if html.html is not None:
            html.html.unwrap()
        # Remove head tag and its content if present
        if html.head is not None:
            html.head.decompose()
        # Remove body tag if present
        if html.body is not None:
            html.body.unwrap()
        paragraph.append(html)
    # If string is not HTML, replace line breaks with <br/> tag and append it to paragraph
    else:
        text = BeautifulSoup('<br/>'.join(string.splitlines()), 'html.parser')
        paragraph.append(text)
    # Append paragraph
    soup.append(paragraph)
    return soup

def df_to_html(data, *args, **kwargs):
    """ Converts pandas DataFrame data to HTML table
        Additional arguments to this function are passed through to pandas method to_html
    """
    table = io.StringIO()
    data.to_html(table, *args, **kwargs)
    return table.getvalue()

def df_to_styled_html(data, caption=None, url_cols=None, **kwargs):
    """ Formats pandas DataFrame data as styled HTML table
    url_cols: List of tuples
        1st element of tuple is name of column that contains url
        2nd element of tuple is name of column that contains name to display for url
    caption: Caption text of table
    kwargs: Specifies styles of table, see styles_dict for valid keyword arguments
    """
    # Default styles
    styles_dict = {
        'cpt_font_color': '#000000',
        'cpt_font_size': 'large',
        'cpt_padding': '5px',
        'cpt_text_align': 'center',
        'tbl_font_size': 'small',
        'tbl_padding': '5px 10px',
        'tbl_text_align': 'left',
        'th_bg_color': '#000000',
        'th_font_color': '#FFFFFF',
        'tr_even_bg_color': '#FFFFFF',
        'tr_odd_bg_color': '#DDDDDD',
    }
    # Read kwargs
    for key in kwargs:
        if key in styles_dict:
            styles_dict[key] = kwargs[key]
        else:
           raise TypeError("df_to_styled_html() got an unexpected keyword argument '{}'"
                           .format(key))
    if url_cols is None:
        url_cols = []
    # Build HTML link
    for elem in url_cols:
        url_col, url_name_col = elem
        data[url_col] = data.apply(
            lambda x: '<a href="{}" target="_blank">{}</a>'.format(x[url_col], x[url_name_col]),
            axis=1
        )
        # Remove column with url names
        del data[url_name_col]
    # Define styles for table
    th_td_style = [
        ('padding', styles_dict['tbl_padding']),
        ('text-align', styles_dict['tbl_text_align']),
        ('font-size', styles_dict['tbl_font_size'])
    ]
    style = [
        {'selector': 'th', 'props': [
            *th_td_style,
            ('font-weight', 'bold'),
            ('background-color', styles_dict['th_bg_color']),
            ('color', styles_dict['th_font_color'])
        ]},
        {'selector': 'td', 'props': th_td_style},
        {'selector': 'caption', 'props': [
            ('color', styles_dict['cpt_font_color']),
            ('text-align', styles_dict['cpt_text_align']),
            ('font-size', styles_dict['cpt_font_size']),
            ('padding', styles_dict['cpt_padding'])
        ]},
        {'selector': '.row_heading, .blank', 'props': [('display', 'none')]}
    ]
    # Set CSS styles defined above
    df_style = data.style.set_table_styles(style)
    # Set style for table
    df_style.set_table_attributes('style="border-collapse: collapse; border: 1px solid black"')
    # Make even rows white
    df_style.set_properties(subset=pd.IndexSlice[::2, :],
                            **{'background-color': styles_dict['tr_even_bg_color']})
    # Make odd rows gray
    df_style.set_properties(subset=pd.IndexSlice[1::2, :],
                            **{'background-color': styles_dict['tr_odd_bg_color']})
    # Add caption
    if caption is not None:
        df_style.set_caption(caption)
    # Return HTML string
    return df_style.render()
