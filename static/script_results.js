"use strict";

const btnSubmitDef = document.querySelector(".btn-submit-definition");

// Submitting the form
document.addEventListener("click", function (e) {
  const element = e.target;
  if (
    element.tagName == "INPUT" &&
    element.classList.contains("btn-submit-definition")
  ) {
    // Making sure that translation field is not empty
    if (document.querySelector("input[name='trans']").value !== "") {
      //   Close the form
      toggleModal();
    }
  }

  // Open the form
  if (
    element.tagName == "BUTTON" &&
    element.classList.contains("add-definition")
  ) {
    toggleModal();
    populateForm();
  }
  // Close the form
  // For x button
  if (
    element.tagName == "BUTTON" &&
    element.classList.contains("btn--close-modal")
  ) {
    toggleModal();
  }
  //   For overlay click
  if (element.tagName == "DIV" && element.classList.contains("overlay")) {
    toggleModal();
  }
});

const modalCustomeDef = document.querySelector(".add-definition-window");
const modalCustomeDefOverlay = document.querySelector(".overlay");

function toggleModal() {
  modalCustomeDefOverlay.classList.toggle("hidden");
  modalCustomeDef.classList.toggle("hidden");
}

// Populate the form field from the URL
function populateForm() {
  // Get the current word
  let params = new URLSearchParams(document.location.search);
  let word = params.get("word");

  //   Populate the word field
  document.querySelector(".form__word").value = word;
}

////////////////////////////////////
// Add and remove word to my word list process(with AJAX)
const btnAddToWordList = document.querySelector(".btn-add-to-list");

btnAddToWordList?.addEventListener("click", function (e) {
  e.preventDefault();

  // Get the current word
  let params = new URLSearchParams(document.location.search);
  let word = params.get("word");
  const Data = {
    word: word,
  };

  // If it is a minus button remove the word
  if (btnAddToWordList.classList.contains("fa-circle-minus")) {
    // Make the AJAX call to remove the word
    $.ajax({
      type: "POST",
      url: "/remove_from_word_list",
      data: JSON.stringify(Data),
      contentType: "application/json",
      dataType: "json",
      success: addToWordList,
    });
  } else {
    // Make the AJAX call to add the word
    $.ajax({
      type: "POST",
      url: "/add_to_word_list",
      data: JSON.stringify(Data),
      contentType: "application/json",
      dataType: "json",
      success: addToWordList,
    });
  }
});

function addToWordList(result) {
  if (result.status) {
    // Change the add to my list btn to added status
    if (btnAddToWordList.classList.contains("fa-circle-plus")) {
      btnAddToWordList.classList.toggle("fa-circle-minus");
      btnAddToWordList.classList.toggle("fa-circle-plus");
      btnAddToWordList.setAttribute("title", "Remove from my word list");
    } else {
      btnAddToWordList.classList.toggle("fa-circle-plus");
      btnAddToWordList.classList.toggle("fa-circle-minus");
      btnAddToWordList.setAttribute("title", "Add to my word list");
    }
  }
}
