import logging

from flask import Blueprint, render_template, request, redirect, session, abort

from models.social_networks import FBAuth, GoogleAuth, LnAuth

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@main_bp.route('/')
def main():
    social = {
        'fb':  FBAuth().get_facebook(request.url_root).url,
        'goo': GoogleAuth().get_goo(request.url_root).url,
        'ln':  LnAuth().get_ln(request.url_root).url
    }
    user = session['user'] if session.get('user') else False
    logger.info(f"====USER_INFO==== {user}")
    return render_template('main.html', soc=social, user=user)


@main_bp.route('/social', defaults={'marker': None}, methods=['POST', 'GET'])
@main_bp.route('/social/<marker>', methods=['POST', 'GET'])
def social_network(marker):
    data = request.args.to_dict()
    if data.get('code'):
        if marker == 'fb':
            user = FBAuth().fetch_info(data.get('code'))
        elif marker == 'goo':
            user = GoogleAuth().fetch_info(data.get('code'),
                                           data.get('state'), request.url_root)
        elif marker == 'ln':
            user = LnAuth().fetch_info(data.get('code'), request.url_root)
        if user:
            session['user'] = user
    else:
        print('NO CODE')

    # if user:
    #     return render_template('main.html', user=user)
    # else:

    return redirect('/')


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@main_bp.route('/profile')
def user_profile():
    if session.get('user'):
        return render_template('user_profile.html')
    else:
        abort(404)


@main_bp.errorhandler(404)
def errofhandler(error):
    print(error)
    return render_template('404.html')
