from requests_oauthlib import OAuth1Session
import os


def generate_tweet_text(title, preprint_url, is_modeling, addressed_rigor, total_rigor, resource_count, open_code, open_data, is_bar_graph, limitations, poor_colormap):
    text = f"The preprint “{title[:50] + ('…' if len(title) > 50 else '')}” ({preprint_url}) has been reviewed by automated tools, find results here: {{}}. We detected "
    tool_notes = []
    if not is_modeling:
        tool_notes.append(f'{addressed_rigor} of {total_rigor} rigor criteria')
    tool_notes.append(f'{resource_count} resource' + ('s' if resource_count != 1 else ''))
    if open_data:
        tool_notes.append('open data')
    if open_code:
        tool_notes.append('open code')
    if is_bar_graph:
        tool_notes.append('potentially misleading graphs')
    if not limitations:
        tool_notes.append('no limitations statement')
    if poor_colormap:
        if len(tool_notes) > 5:
            tool_notes.append('other issues')
        else:
            tool_notes.append('a problematic colormap')
    if len(tool_notes) < 3:
        text = text + ' and '.join(tool_notes)
    else:
        text = text + ', '.join(tool_notes[:-1]) + ', and ' + tool_notes[-1]
    return text + '.'


def update_twitter_status(text):
    session = OAuth1Session(os.environ['TWITTER_CLIENT_KEY'],
                            os.environ['TWITTER_CLIENT_SECRET'],
                            os.environ['TWITTER_OWNER_KEY'],
                            os.environ['TWITTER_OWNER_SECRET'])
    r = session.post('https://api.twitter.com/1.1/statuses/update.json', params={'status': text})
    if r.status_code != 200:
        raise Exception('Twitter error', r.status_code, r.text)
