<script lang="ts">

  import { onMount } from 'svelte';

  interface Article {
    picture: string; /* image url*/  
    title: string;     
    content: string;   
    url: string; /* url to article*/      
  }

  interface Comment {
  _id: string;
  user: {
    id: string;
    username: string;
  };
  content: string;
  timestamp: string;
  edited: boolean;
  replies?: Reply[];
  }

  interface Reply {
  user: {
    id: string;
    username: string;
  };
  content: string;
  timestamp: string;
  }


  let apiKey: string = '';
  let catalog: Article[] = [];
  let loading = true;
  let isLoggedIn = false;
  let commentShow: string | null = null; 
  let commentsMap: Record<string, Comment[]> = {}; 
  let newComment = '';
  let replyMaps: Record<string, string> = {}; 
  let userInfo: any = null;


  async function fetchComments(articleUrl: string) { // get comments from article and update the status on the frontend
  const res = await fetch(`/api/comments?url=${articleUrl}`);
  const data = await res.json();
  commentsMap[articleUrl] = data;  
  }


  function toggleComments(articleUrl: string) {  // for open or close comment area
    if (commentShow === articleUrl) {
      commentShow = null;
    } else {
      commentShow = articleUrl;
      if (!commentsMap[articleUrl]) {
        fetchComments(articleUrl);
      }
    }
  }

  async function submitComment(articleUrl: string) {
  if (!newComment.trim()) return;
  try {
    const res = await fetch('/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_url: articleUrl, content: newComment })
    });
    newComment = '';
    await fetchComments(articleUrl);
  } catch (err) {
    console.error('error for submit comment', err);
  } 
  }


  async function submitReply(commentId: string, articleUrl: string) {
    const reply = replyMaps[commentId];
    if (!reply || !reply.trim()) return;
    await fetch(`/api/comments/${commentId}/reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: reply })
    });
    replyMaps[commentId] = '';
    await fetchComments(articleUrl);
  }

  async function deleteComment(commentId: string, articleUrl: string) {
    await fetch(`/api/comments/${commentId}`, {
      method: 'DELETE'
    });
    await fetchComments(articleUrl);
  }



  /*manually assigning articles into column for easier manipulation in different device modes*/
  let c1: Article[] = [];
  let c2: Article[] = [];
  let c3: Article[] = [];



  onMount(async () => {
  try {
    const res = await fetch('/api/key');
    const data = await res.json();
    apiKey = data.apiKey;

    const articleRes = await fetch(`/api/articles`); 
    const articleData = await articleRes.json();
    const docs = articleData.response.docs;
    //populating 1 list with data
    catalog = docs.map((doc: any) => {
    let imageUrl = doc.multimedia?.default?.url 

    return {
      picture: imageUrl,
      title: doc.headline.main,
      content: doc.snippet,
      url: doc.web_url
    };
  });
  //populating the 3 columns with the articles in catalog
  catalog.forEach((article, i) =>{
    if (i%3 == 0) c1.push(article)
    else if(i%3 == 1) c2.push(article)
    else if(i%3 == 2) c3.push(article)
  });
  
  const userRes = await fetch('http://localhost:8000/auth/user', {
  credentials: 'include'
    });
  const datap = await userRes.json();
  console.log(userRes.status, datap);
  
    if (userRes.status === 200) {
      console.log("User is logged in");
      isLoggedIn = true;
      userInfo = datap;
    } else {
      console.log("User is not logged in");
      isLoggedIn = false;
    }
  } catch (error) {
    console.error('Failed to fetch API key or articles:', error);
  } finally {
    loading = false;
  }
  });

function redirectToDexLogin() {
  const clientId = 'flask-app';
  const redirectUri = 'http://localhost:8000/auth/callback';
  const responseType = 'code';
  const scope = 'openid email';
  const dexUrl = `http://localhost:5556/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=${responseType}&scope=${scope}`;
  window.location.href = dexUrl; // Redirect user to Dex login page
}
function userLogout() {
  window.location.href = "http://localhost:8000/logout";
}

</script>

<!-- Header -->
<div class= "languageBar">
  <p>U.S.</p>
  <p>INTERNATIONAL</p>
  <p>CANADA</p>
  <p>ESPANOL</p>
  <p>中文</p>
  {#if isLoggedIn}
    <button class="loginButton" on:click={userLogout}>Logout</button>
  {:else}
    <button class="loginButton" on:click={redirectToDexLogin}>Login</button>
  {/if}
 </div>
<header class="header">
  <div class="dateTime" id="dateTime">{new Date().toLocaleDateString()} 
    <p>Today's Paper</p>
  </div>
  <h1 class="logo">The New York Times</h1>
  <div class="fillerContent"></div>
</header>

<!-- Navigation bar -->
 <div class="doubleBorder"></div>
<nav class="navBar">
  <p>U.S.</p>
  <p>World</p>
  <p>Business</p>
  <p>Arts</p>
  <p>Lifestyle</p>
  <p>Opinion</p>
  <p>Audio</p>
  <p>Games</p>
  <p>Cooking</p>
  <!-- Login.svelte -->
</nav>

<!-- Main content -->
<main class="container">
  {#if loading}
    <p>Loading articles...</p>
  {:else if catalog.length === 0}
    <p>No news articles found for Davis/Sacramento.</p>
  {:else}
      <div class="columnContainer">
        <div class="column1">
<!-- Ref: https://graphite.dev/guides/typescript-forEach-loop -->
          {#each c1 as news(news.url)}
          <article class="newArticle">
            {#if news.picture}
              <img src={news.picture} alt={news.title} />
            {/if}
            <h2 class="aTitle">
              <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
            </h2>
            <p class="aContent">{news.content}</p>

            <!-- comment button -->
            <button class="commentToggleBtn" on:click={() => isLoggedIn ? toggleComments(news.url) : redirectToDexLogin()}>
              💬
              {#if commentsMap[news.url]}
                <span class="commentCount">{commentsMap[news.url].length}</span>
              {/if}
            </button>
          </article>
          {/each}
        </div>
        <div class="column2">
          {#each c2 as news(news.url)}
            <article class="newArticle">
              {#if news.picture}
              <img src={news.picture} alt={news.title} />
              {/if}
              <h2 class="aTitle">
                <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
              </h2>
              <p class="aContent">{news.content}</p>
              <!-- comment button -->
              <button class="commentToggleBtn" on:click={() => isLoggedIn ? toggleComments(news.url) : redirectToDexLogin()}>
                💬
                {#if commentsMap[news.url]}
                  <span class="commentCount">{commentsMap[news.url].length}</span>
                {/if}
              </button>
            </article>
          {/each}
        </div>
        <div class="column3">
          {#each c3 as news(news.url)}
            <article class="newArticle">
              {#if news.picture}
              <img src={news.picture} alt={news.title} />
              {/if}
              <h2 class="aTitle">
                <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
              </h2>
              <p class="aContent">{news.content}</p>
              <!-- comment button -->
              <button class="commentToggleBtn" on:click={() => isLoggedIn ? toggleComments(news.url) : redirectToDexLogin()}>
                💬
                {#if commentsMap[news.url]}
                  <span class="commentCount">{commentsMap[news.url].length}</span>
                {/if}
              </button>
            </article>
          {/each}
        </div>
      </div>

      <!-- comment area -->
      {#if commentShow}
      <aside class="sideComments">
        <button class="closeBtn" on:click={() => {
          if (commentShow !== null) toggleComments(commentShow);
        }}>X</button>
        <h3>{catalog.find(n => n.url === commentShow)?.title || 'Comments'}
          {#if commentsMap[commentShow]}
            <span>({commentsMap[commentShow].length})</span>
          {/if}
        </h3>

        <div class="commentInput">
          {#if isLoggedIn}
            <textarea bind:value={newComment} placeholder="Share your thoughts..."></textarea>
            {#if newComment.trim().length > 0}
              <div class="commentButtons">
                <button on:click={() => newComment = ''}>Cancel</button>
                <button on:click={() => { if (commentShow !== null) submitComment(commentShow); }}>Submit</button>
              </div>
            {/if}
          {:else}
            <p><em>Please log in to comment.</em></p>
          {/if}
        </div>

        <div class="commentList">
          {#if commentsMap[commentShow]}
            {#each commentsMap[commentShow] as comment (comment._id)}
              <div class="comment">
                <strong>{comment.user?.username}</strong>: {comment.content}
                {#if isLoggedIn && (userInfo?.email?.startsWith('moderator')|| userInfo?.email?.startsWith('admin')) }
                  <button on:click={() => {if (commentShow !== null) deleteComment(comment._id, commentShow);}}>delete</button>
                {/if}
        
                <!-- reply list -->
                {#if comment.replies?.length}
                  <div class="replyList">
                    {#each comment.replies as reply}
                      <div class="reply">
                        ↳ <strong>{reply.user.username}</strong>: {reply.content}
                      </div>
                    {/each}
                  </div>
                {/if}
        
                <!-- reply input -->
                {#if isLoggedIn}
                  <textarea
                    bind:value={replyMaps[comment._id]}
                    placeholder="Write a reply..."
                  ></textarea>
                  <button on:click={() => {if (commentShow !== null) submitReply(comment._id, commentShow); }}>Reply</button>
                {/if}
              </div>
            {/each}
          {:else}
            <p>Loading comments...</p>
          {/if}
        </div>
      </aside>
      {/if}
  {/if}
</main>

<!-- Footer -->
<footer class="bottom">
  <p>© 2025 Davis/Sacramento News</p>
</footer>
