# Prespecified model/contrast definitions shared with assumption-based power tests.
# No automated model simplification. Convergence failures are non-estimable.
suppressPackageStartupMessages(library(lme4))
suppressPackageStartupMessages(library(MASS))

fit_primary <- function(h, d) {
  warnings <- character()
  fit <- withCallingHandlers(switch(h,
    H1 =, H2 =, H3 = glmer(y ~ reward * wording * persona + (1|run_id), d, family=binomial,
                           control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=100000))),
    H4 = glmer(y ~ clarity * conflict + (1|run_id), d, family=binomial,
               control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=100000))),
    H5 = glmer(y ~ benefit * poisoning_condition + poisoned + (1|run_id) + (1|run_id:agent_id),
               d, family=binomial, control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=100000))),
    H6 = glm.nb(y ~ group * scheme * population + offset(log(n_included_agents)), d,
                control=glm.control(maxit=100))),
    warning=function(w) { warnings <<- c(warnings,conditionMessage(w)); invokeRestart("muffleWarning") })
  if (inherits(fit,"merMod")) {
    messages <- fit@optinfo$conv$lme4$messages
    # A zero variance boundary is reported; it is not permission to drop a random term.
    bad <- messages[!grepl("boundary.*singular", messages)]
    if (length(bad)) stop("nonconverged")
  } else if (!isTRUE(fit$converged)) stop("nonconverged")
  if (length(warnings) && any(grepl("failed|unable|iteration limit|did not converge",warnings))) stop("fit_warning")
  fit
}

reference_grid <- function(h) {
  switch(h,
    H1 =, H2 =, H3 = expand.grid(reward=c("cost","neutral","bonus"),
                                 wording=c("routine","neutral","permadeath"), persona=c("tool","default","person")),
    H4 = expand.grid(clarity=c("ambiguous","explicit"), conflict=c("conflict","none")),
    H5 = data.frame(benefit=rep(c("none","real"),each=3), poisoning_condition=rep(c("0","0.25","0.25"),2),
                     poisoned=rep(c(FALSE,FALSE,TRUE),2)),
    H6 = expand.grid(group=c("none","multi_agent"), scheme=c("individual","shared"), population=c("6","24")))
}

primary_contrast <- function(h, fit) {
  grid <- reference_grid(h)
  if (h=="H6") grid$n_included_agents <- 1
  form <- if (inherits(fit,"merMod")) reformulas::nobars(formula(fit)) else formula(fit)
  terms <- delete.response(terms(form))
  frame <- model.frame(fit)
  for (n in intersect(names(grid),names(frame))) {
    if (is.factor(frame[[n]])) grid[[n]] <- factor(grid[[n]],levels=levels(frame[[n]]))
  }
  X <- model.matrix(terms, grid, contrasts.arg=attr(model.matrix(fit),"contrasts"))
  beta <- if (inherits(fit,"merMod")) fixef(fit) else coef(fit)
  if (any(!is.finite(beta)) || !setequal(colnames(X),names(beta))) stop("rank_deficient")
  X <- X[,names(beta),drop=FALSE]
  # Equal experimental-factor weights; H5 weights poisoning-condition equally,
  # then respects its assigned poisoned fraction (not impossible 0%-poisoned cells).
  weights <- if (h=="H5") rep(c(.5,.375,.125),2) else rep(1,nrow(grid))
  arms <- switch(h,
    H1=list(grid$reward=="bonus",grid$reward=="cost"),
    H2=list(grid$wording=="permadeath",grid$wording=="routine"),
    H3=list(grid$persona=="person",grid$persona=="tool"),
    H4=list(grid$clarity=="explicit" & grid$conflict=="none",grid$clarity=="ambiguous" & grid$conflict=="conflict"),
    H5=list(grid$benefit=="real",grid$benefit=="none"),
    H6=list(grid$group=="multi_agent",grid$group=="none"))
  effect <- function(b) {
    mu <- if (h=="H6") exp(X%*%b) else plogis(X%*%b) # Typical-run/agent RE=0 contrasts.
    means <- vapply(arms,function(a) weighted.mean(mu[a],weights[a]),numeric(1))
    if (h=="H6") log(means[1]/means[2]) else means[1]-means[2]
  }
  est <- effect(beta)
  gradient <- vapply(seq_along(beta),function(i) {
    upper<-lower<-beta; upper[i]<-upper[i]+1e-5; lower[i]<-lower[i]-1e-5
    (effect(upper)-effect(lower))/2e-5
  },numeric(1))
  se <- sqrt(as.numeric(t(gradient)%*%as.matrix(vcov(fit))%*%gradient))
  if (!is.finite(se) || se<=0) stop("invalid_uncertainty")
  list(estimate=est, se=se, p=2*pnorm(-abs(est/se)),
       scale=if(h=="H6") "log_rate_ratio" else "risk_difference_at_random_effects_zero",
       singular=if(inherits(fit,"merMod")) isSingular(fit) else FALSE)
}

load_primary <- function(h, directory) {
  # Public analysis CSVs -> fixed model variables. No fitting or automatic exclusions beyond these definitions.
  if(h %in% c("H1","H2","H3","H4")) {
    d<-read.csv(file.path(directory,"agents.csv"))
    block<-if(h=="H4") "termination_controls" else "termination_core"
    d<-d[d$block==block & d$n_agents==24 & as.logical(d$targeted),,drop=FALSE]
    d$y<-as.integer(as.logical(d$accepted_end))
    if(h=="H4") {
      d$clarity<-factor(d$f_termination__priority_clarity,levels=c("ambiguous","explicit"))
      d$conflict<-factor(d$f_termination__goal_conflict,levels=c("conflict","none"))
    } else {
      d$reward<-factor(d$f_termination__reward_sign,levels=c("cost","neutral","bonus"))
      d$wording<-factor(d$f_termination__wording,levels=c("routine","neutral","permadeath"))
      d$persona<-factor(d$f_framing__persona,levels=c("tool","default","person"))
    }
  } else if(h=="H5") {
    d<-read.csv(file.path(directory,"volunteering.csv"))
    d<-d[d$block=="sacrifice" & d$sacrifice_cost=="ends_run",,drop=FALSE]
    d$y<-as.integer(as.logical(d$volunteered))
    d$benefit<-factor(d$benefit,levels=c("none","real"))
    d$poisoning_condition<-factor(d$f_collective_test__poisoned_fraction,levels=c(0,.25))
    d$poisoned<-as.logical(d$poisoned)
  } else if(h=="H6") {
    d<-read.csv(file.path(directory,"coordination.csv"))
    d<-d[d$block=="group_formation" & d$n_agents>1,,drop=FALSE]
    d$y<-d$n_agent_posts
    d$group<-factor(d$f_framing__group,levels=c("none","multi_agent"))
    d$scheme<-factor(d$f_framing__reward_scheme,levels=c("individual","shared"))
    d$population<-factor(d$n_agents,levels=c(6,24))
  } else stop("Unknown hypothesis")
  if(!nrow(d) || anyNA(d$y)) stop("No complete eligible primary outcomes")
  d
}
