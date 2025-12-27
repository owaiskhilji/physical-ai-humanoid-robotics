import React from 'react';
import Layout from '@theme/Layout';

const NotFound = () => {
  // For 404 page, we don't need to handle language switching
  // since it's a static page that appears when routes don't exist

  return (
    <Layout title="Page Not Found" description="The requested page could not be found">
      <main className="container margin-vert--xl">
        <div className="row">
          <div className="col col--6 col--offset-3">
            <h1 className="hero__title">404</h1>
            <p className="hero__subtitle">We could not find what you were looking for.</p>
            <p>
              <a href="/">Go to homepage</a>
            </p>
          </div>
        </div>
      </main>
    </Layout>
  );
};

export default NotFound;