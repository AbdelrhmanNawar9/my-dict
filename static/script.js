// Log in process
document.querySelector(".btn-login")?.addEventListener("click", function (e) {
  e.preventDefault();
  const logInData = {
    userName: document.querySelector("#username").value,
    password: document.querySelector("#password").value,
  };
  $.ajax({
    type: "POST",
    url: "/login",
    data: JSON.stringify(logInData),
    contentType: "application/json",
    dataType: "json",
    success: message,
  });
});

function message(result) {
  console.log(result);
  if (!result.message) {
    window.location.href = "/";
  } else {
    document.querySelector(
      ".login-message"
    ).innerHTML = `<p>${result.message}</p>`;
  }
}

// Register process
document
  .querySelector(".btn-register")
  ?.addEventListener("click", function (e) {
    e.preventDefault();
    const Data = {
      userName: document.querySelector("#username")?.value,
      password: document.querySelector("#password")?.value,
      passwordConfirmation: document.querySelector("#password-confirmation")
        ?.value,
    };
    $.ajax({
      type: "POST",
      url: "/register",
      data: JSON.stringify(Data),
      contentType: "application/json",
      dataType: "json",
      success: message,
    });
  });
