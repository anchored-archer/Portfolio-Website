import { Octokit } from "https://esm.sh/octokit";

async function get_user_repositories(username) {
  const octokit = new Octokit({});

  let result = await octokit.request("GET /users/{username}/repos", {
    username: username,
    headers: {
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });

  console.log(result);
  return result;
}

function update_screen(elements) {
  let div = document.querySelector(".display-results");
  console.log(div, elements);
  div.innerHTML = elements;
}

function make_repo_array(array) {
  let values = ["name", "full_name", "description", "language"];
  let repo_array = [];
  for (let dict of array) {
    let dictionary = {};
    for (let key in dict) {
      if (values.includes(key) == true) {
        dictionary[key] = dict[key];
      }
    }
    repo_array.push(dictionary);
  }
  return repo_array;
}

function make_elements(repo_info) {
  let elements = "";
  for (let i of repo_info) {
    let title = i["name"];
    let tags = i["language"];
    let description = i["description"];
    let link = `https://github.com/${i["full_name"]}`;

    let element = `<div class=\'card ms-2 me-2\' style=\'width: 18rem;\'>\
  <div class=\'card-body\'>\
    <h5 class=\'card-title\'>${title}</h5>\
    <h6 class=\'card-subtitle \'>${tags}</h6>\
    <p class=\'card-text\'>${description}</p>\
    <a href=\'${link}\' class=\'btn btn-primary\'>Visit Webpage!</a>\
  </div>\
</div>`;

    elements += element;
  }
  return elements;
}

async function load_web() {
  let user_repos = get_user_repositories("Wandering-Explorer");
  user_repos
    .then((responce) => {
      let cleaned_repo_array = make_repo_array(responce.data);
      let elements = make_elements(cleaned_repo_array);
      localStorage.setItem("elements", elements);
      let time = new Date().getTime();
      localStorage.setItem("time", time);
      update_screen(elements);
    })
    .catch((err) => {
      console.log(err);
    });
}

// When User Quites Website: (look up the docs for refernce)
if (document.visibilityState !== "visible") {
  let time = new Date().getTime();
  localStorage.setItem("time", time);

  // When User Opens Website For The First Time:
} else {
  let last_opened = localStorage.getItem("time");
  if (last_opened == null) {
    load_web();
  } else {
    // If user Reopened Website after 30m
    let time_now = new Date().getTime();
    if (time_now - last_opened >= 1800000) {
      load_web();
    } else {
      // If User Reopend Website within 30m of their intial opening
      let elements = localStorage.getItem("elements");
      update_screen(elements);
    }
  }
}



document.addEventListener("visibilitychange", () => {
  // When User Quites Website: (look up the docs for refernce)
  if (document.visibilityState !== "visible") {
    let time = new Date().getTime();
    localStorage.setItem("time", time);

    // When User Opens Website For The First Time:
  } else {
    let last_opened = localStorage.getItem("time");
    if (last_opened == null) {
      load_web();
    } else {
      // If user Reopened Website after 30m
      let time_now = new Date().getTime();
      if (time_now - last_opened >= 1800000) {
        load_web();
      } else {
        // If User Reopend Website within 30m of their intial opening
        let elements = localStorage.getItem("elements");
        update_screen(elements);
      }
    }
  }
});
  