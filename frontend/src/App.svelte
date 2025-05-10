<script lang="ts">
  import { onMount } from 'svelte';

  interface Article {
    picture: string; /* image url*/  
    title: string;     
    content: string;   
    url: string; /* url to article*/      
  }

  let apiKey: string = '';
  let catalog: Article[] = [];
  let loading = true;

  /*manually assigning articles into column for easier manipulation in different device modes*/
  let c1: Article[] = [];
  let c2: Article[] = [];
  let c3: Article[] = [];

  onMount(async () => {
  try {
    const res = await fetch('/api/key');
    const data = await res.json();
    apiKey = data.apiKey;

    const articleRes = await fetch(`https://api.nytimes.com/svc/search/v2/articlesearch.json?q=Sacramento%20AND%20Davis&api-key=${apiKey}`);
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
  } catch (error) {
    console.error('Failed to fetch API key or articles:', error);
  } finally {
    loading = false;
  }
});

</script>

<!-- Header -->
 <div class= "languageBar">
  <p>U.S.</p>
  <p>INTERNATIONAL</p>
  <p>CANADA</p>
  <p>ESPANOL</p>
  <p>中文</p>
  <!-- Login.svelte -->
<a href="http://localhost:5556/auth?client_id=svelte-app&redirect_uri=http://localhost:5173/callback&response_type=code&scope=openid email profile">
  SIGN IN HERE
</a>
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
            <article class = "newArticle">
              {#if news.picture}
              <img src={news.picture} alt={news.title} />
            {/if}
            <h2 class="aTitle">
              <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
            </h2>
            <p class="aContent">{news.content}</p>
            </article>
            {/each}
        </div>
        <div class="column2">
          {#each c2 as news(news.url)}
            <article class = "newArticle">
              {#if news.picture}
              <img src={news.picture} alt={news.title} />
            {/if}
            <h2 class="aTitle">
              <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
            </h2>
            <p class="aContent">{news.content}</p>
            </article>
            {/each}
        </div>
        <div class="column3">
          {#each c3 as news(news.url)}
            <article class = "newArticle">
              {#if news.picture}
              <img src={news.picture} alt={news.title} />
            {/if}
            <h2 class="aTitle">
              <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
            </h2>
            <p class="aContent">{news.content}</p>
            </article>
            {/each}
        </div>
       </div>
       {/if}
</main>

<!-- Footer -->
<footer class="bottom">
  <p>© 2025 Davis/Sacramento News</p>
</footer>