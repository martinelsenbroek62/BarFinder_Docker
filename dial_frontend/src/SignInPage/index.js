import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import * as Yup from 'yup';
import {Formik} from 'formik';
import {Row, Col, Form, Button} from 'react-bootstrap';
import {LinkContainer} from 'react-router-bootstrap';

import {userActions} from '../_actions';

const schema = Yup.object().shape({
    email: Yup.string().email().required(),
    password: Yup.string().required()
}).required();

class SignInPage extends React.Component {

    static propTypes = {
        signingIn: PropTypes.bool.isRequired,
        error: PropTypes.string,
        signin: PropTypes.func.isRequired
    }

    constructor() {
        super(...arguments);

        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit({email, password}) {
        const {signin} = this.props;

        if (email && password) {
            signin(email, password);
        }
    }

    render() {
        const {signingIn, error: serverError} = this.props;
        return
    <
        Row >
        < Col
        sm = {8}
        xs = {12} >
            < h1 > Sign
        In < /h1>
        < hr / >
        < Formik
        validationSchema = {schema}
        onSubmit = {this.handleSubmit}
        initialValues = {
        {
            email: '',
                password
        :
            ''
        }
    }>
        {
            (({
                  handleSubmit,
                  handleChange,
                  values,
                  isValid,
                  errors
              }) => (
                < Form
            noValidate
            onSubmit = {handleSubmit} >
                < Form.Group
            controlId = "formSignInEmail" >
                < Form.Label > Email < /Form.Label>
                < Form.Control
            type = "email"
            name = "email"
            placeholder = "Enter email"
            value = {values.email}
            onChange = {handleChange}
            isInvalid = {
            !!serverError || !!errors.email
        }
            />
            < Form.Control.Feedback
            type = "invalid" >
                {serverError}
            {
                errors.email
            }
        <
            /Form.Control.Feedback>
            < /Form.Group>
            < Form.Group
            controlId = "formSignInPassword" >
                < Form.Label > Password < /Form.Label>
                < Form.Control
            type = "password"
            name = "password"
            placeholder = "Password"
            value = {values.password}
            onChange = {handleChange}
            isInvalid = {
            !!errors.password
        }
            />
            < Form.Control.Feedback
            type = "invalid" >
                {errors.password}
                < /Form.Control.Feedback>
                < /Form.Group>
                < Form.Group >
                < Button
            variant = "primary"
            type = "submit"
            disabled = {signingIn} >
                Sign
            In
            < /Button>
            < LinkContainer
            to = "/signup/" >
                < Button
            variant = "link" > Sign
            Up < /Button>
            < /LinkContainer>
            < /Form.Group>
            < /Form>
        ))
        }
    <
        /Formik>
        < /Col>
        < /Row>;

    }

}

function mapState(state) {
    const {signingIn, error} = state.auth;
    return {signingIn, error};
}

const actionCreators = {
    signin: userActions.signin
};

export default connect(mapState, actionCreators)(SignInPage);
