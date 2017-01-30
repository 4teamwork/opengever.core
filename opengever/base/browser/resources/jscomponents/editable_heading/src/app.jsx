import React from 'react';
import 'whatwg-fetch'

class EditableTitle extends React.Component {

  constructor(props) {
    super(props)

    var initTitle = document.querySelector("h1.documentFirstHeading").textContent
    this.state = {editing: false,
                  title: initTitle
                }

    this.submitHandler = this.submitHandler.bind(this)
    this.editHandler = this.editHandler.bind(this)
  }

  editHandler(event){
    event.preventDefault()
    this.setState({editing: true})
  }

  submitHandler(event){
    event.preventDefault()
    const title = this.refs.title.value
    let payload = {
      title: title
    }

    let options = {
      credentials: 'same-origin',
      headers: new Headers({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }),
      body: JSON.stringify(payload),
      method: 'PATCH'
    }

    fetch('.', options)
      .then(response => {
        this.setState({editing: false, title: title})
      })
  }

  render() {
    if (this.state.editing) {

      return (
          <form onSubmit={this.submitHandler}>
            <input autoFocus
                   name="title"
                   placeholder="Title is required"
                   ref="title"
                   defaultValue={this.state.title} />
            <input type="submit" value="Save" />
          </form>
      )

    } else {

      return (
        <div>
          <h1 className="documentFirstHeading">{this.state.title}</h1>
          <div className="editButton">
            <a href="#" onClick={this.editHandler}>edit</a>          
          </div>
        </div>
      )

    }
  }
}


export default EditableTitle
