export interface Article {
    picture: string;
    title: string;
    content: string;
    url: string;
  }
  //Raw data fetched from the API are stored in docs and then transformed into Article objects
  //Shoukd return a list of Article[] objects
  export function mappingDocsToArticles(docs: any[]): Article[] {
    return docs.map((doc: any) => {
      let imageUrl = doc.multimedia?.default?.url
      //image issue, some articles don't have images
      return {
        picture: imageUrl,
        title: doc.headline.main,
        content: doc.snippet,
        url: doc.web_url
      };
    });
  }