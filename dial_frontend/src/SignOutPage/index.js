import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {Alert} from 'react-bootstrap';

import {userActions} from '../_actions';


class SignOutPage extends React.Component {

    static propTypes = {
        signedIn: PropTypes.bool.isRequired,
        signout: PropTypes.func.isRequired
    }

    constructor() {
        super(...arguments);
        const {signedIn, signout} = this.props;
        if (signedIn) {
            signout();
        }
    }

    render() {
        return
    <
        Alert
        variant = "warning" >
            < Alert.Heading > Your
        account
        is
        not
        logged in < /Alert.Heading>
        < hr / >
        < p >
        Hmm, it
        seems
        your
        account
        is
        not
        logged in
    .
        No
        action
        will
        be
        taken.
        < /p>
        < /Alert>;
    }

}


function mapState(state) {
    const {signedIn} = state.auth;
    return {signedIn};
}

const actionCreators = {
    signout: userActions.signout
};

export default connect(mapState, actionCreators)(SignOutPage);
